import numpy as np
from qiskit import QuantumCircuit

def build_circuit(kind, n=3):
    if kind == "Bell State":
        qc = QuantumCircuit(2, 2)
        qc.h(0); qc.cx(0, 1); qc.measure([0,1], [0,1])
    elif kind == "GHZ State":
        n = max(3, min(int(n), 8))
        qc = QuantumCircuit(n, n)
        qc.h(0)
        for i in range(1, n): qc.cx(0, i)
        qc.measure(range(n), range(n))
    elif kind == "Superposition":
        n = max(1, min(int(n), 8))
        qc = QuantumCircuit(n, n)
        for i in range(n): qc.h(i)
        qc.measure(range(n), range(n))
    else:
        qc = QuantumCircuit(2, 2)
        qc.h(0); qc.x(1); qc.cx(0,1); qc.measure([0,1],[0,1])
    return qc

def circuit_metrics(qc):
    return {
        "Qubits": qc.num_qubits,
        "Classical bits": qc.num_clbits,
        "Gates": len(qc.data),
        "Depth": qc.depth(),
        "Measurements": sum(1 for item in qc.data if item.operation.name == "measure"),
    }

def simulate(qc, shots=1024):
    from qiskit_aer import AerSimulator
    result = AerSimulator().run(qc, shots=shots).result()
    return result.get_counts()
