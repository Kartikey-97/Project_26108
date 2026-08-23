import { MOCK_LED_LIGHTING_DATA } from '../data/mockProcurementData';

// API Client Abstraction Layer for SIH 2026 Unified Procurement Intelligence Workspace
export async function analyzeProcurementInput({ text, file, inputType = 'text', category = 'LED Street Lighting', useLiveBackend = false }) {
  if (useLiveBackend) {
    try {
      const response = await fetch('/api/v1/procurement/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          raw_text: text,
          input_type: inputType,
          category_hint: category
        })
      });
      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }
      return await response.json();
    } catch (err) {
      console.warn('Backend API connection failed, falling back to PoC mock dataset:', err);
      // Fallback gracefully
    }
  }

  // Standalone Mock Mode for Proof of Concept (LED Street Lighting)
  return new Promise((resolve) => {
    setTimeout(() => {
      // Return realistic mock data
      resolve(MOCK_LED_LIGHTING_DATA);
    }, 1200);
  });
}
