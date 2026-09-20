with open('frontend/src/pages/NewAnalysisPage.tsx', 'r') as f:
    content = f.read()

old_button = """                  onClick={handleStartExtraction}
                  disabled={!isInputValid}
                  rightIcon={<ArrowRight size={15} />}
                  className="shadow-soft active:scale-[0.98] transition-transform"
                >
                  {(!isBackendReady && !demoFixture) ? 'Waking Backend (~50s)...' : 'Extract Procurement Profile'}"""

new_button = """                  onClick={handleStartExtraction}
                  disabled={!isInputValid || (!isBackendReady && !demoFixture)}
                  rightIcon={<ArrowRight size={15} />}
                  className="shadow-soft active:scale-[0.98] transition-transform"
                >
                  {(!isBackendReady && !demoFixture) ? 'Waking Backend (~50s)...' : 'Extract Procurement Profile'}"""

if old_button in content:
    content = content.replace(old_button, new_button)
    with open('frontend/src/pages/NewAnalysisPage.tsx', 'w') as f:
        f.write(content)
    print("Fixed button")
else:
    print("Could not find button block")
