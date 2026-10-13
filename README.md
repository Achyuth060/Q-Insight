# Q-Insight — IBM Quantum Job Monitoring & Analytics Dashboard

End-semester capstone MVP for the problem statement: build a dashboard showing live/public IBM Quantum jobs.

## Features
- IBM Quantum job monitoring through Qiskit Runtime
- Demo mode when IBM credentials are not configured
- KPI dashboard
- Job filtering and searchable table
- Backend analytics
- Historical analytics from locally collected snapshots
- Quantum circuit analyzer with Bell/GHZ/custom examples
- Lightweight queue-time prediction using historical/demo data

## Run
```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Real IBM Quantum mode
1. Create an IBM Quantum Platform account/API key.
2. Get your instance CRN.
3. Copy `.env.example` to `.env` and fill in the values.
4. Restart Streamlit.

IBM currently recommends `QiskitRuntimeService(channel="ibm_quantum_platform", token=..., instance=...)` for authenticated access.

## Demo mode
If credentials are absent, the dashboard clearly labels itself as DEMO MODE and uses deterministic sample records so the UI can be developed and demonstrated safely. Do not claim demo records are live IBM records.
