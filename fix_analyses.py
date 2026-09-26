import re

with open('backend/kartikey/api/routes/analyses.py', 'r') as f:
    content = f.read()

# 1. Fix base_designation collision in get_analysis
old_match = "superseding = next((s for s in store.list_all() if normalize_designation(s.base_designation) == norm_target), None)"
new_match = "superseding = next((s for s in store.list_all() if (s.is_number and normalize_designation(s.is_number) == norm_target) or (hasattr(s, 'designation') and normalize_designation(s.designation) == norm_target)), None)"
content = content.replace(old_match, new_match)

# 2. Add background task spawn in trigger_manual_bis_sync
sync_block_old = """
        def do_sync() -> None:
            \"\"\"Blocking BIS HTTP calls — run off event loop via asyncio.to_thread.\"\"\"
            config = BISClientConfig(timeout_seconds=15.0, max_retries=1)
            with BISClient(config=config) as client:
                svc = BISSyncService(client=client, standards_store=store)
                for is_num in is_numbers:
                    res = svc.sync_designation(is_num)
                    record_sync_result(
                        is_number=is_num,
                        synced_at=datetime.now(timezone.utc),
                        changed=res.changed,
                        errors=res.errors,
                        analysis_id=analysis_id,
                    )

        # Bug fix: must await asyncio.to_thread so the coroutine is actually scheduled
        await asyncio.to_thread(do_sync)
        return {"status": "sync_complete", "standards_synced": is_numbers}"""

sync_block_new = """
        def do_sync() -> list:
            \"\"\"Blocking BIS HTTP calls — run off event loop via asyncio.to_thread.\"\"\"
            new_superseded = []
            config = BISClientConfig(timeout_seconds=15.0, max_retries=1)
            with BISClient(config=config) as client:
                svc = BISSyncService(client=client, standards_store=store)
                for is_num in is_numbers:
                    res = svc.sync_designation(is_num)
                    if res.supersedes:
                        new_superseded.append(res.supersedes)
                    record_sync_result(
                        is_number=is_num,
                        synced_at=datetime.now(timezone.utc),
                        changed=res.changed,
                        errors=res.errors,
                        analysis_id=analysis_id,
                    )
            return new_superseded

        # Bug fix: must await asyncio.to_thread so the coroutine is actually scheduled
        new_superseded_ids = await asyncio.to_thread(do_sync)
        
        if new_superseded_ids:
            from kartikey.orchestration.pipeline import rescore_and_merge
            from kshiraj.bis_live_ingestion.normalizer import normalize_designation
            
            for sup_is in new_superseded_ids:
                norm_sup = normalize_designation(sup_is)
                # Find it in the store
                new_std = next((s for s in store.list_all() if (s.is_number and normalize_designation(s.is_number) == norm_sup) or (hasattr(s, 'designation') and normalize_designation(s.designation) == norm_sup)), None)
                if new_std:
                    asyncio.create_task(rescore_and_merge(analysis_id, new_std))

        return {"status": "sync_complete", "standards_synced": is_numbers}"""

if sync_block_old in content:
    content = content.replace(sync_block_old, sync_block_new)
    with open('backend/kartikey/api/routes/analyses.py', 'w') as f:
        f.write(content)
    print("Replaced analyses.py successfully.")
else:
    print("Old sync block not found! Checking if it differs.")
    import sys
    sys.exit(1)
