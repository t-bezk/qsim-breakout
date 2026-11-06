"""Grover's algorithm for small number of qubits"""

import math
import sys
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector


def phase_flip(qc, n):
    if n == 1:
        qc.z(0)
    else:
        qc.h(n - 1)
        qc.mcx(list(range(n - 1)), n - 1)
        qc.h(n - 1)


def oracle(n, marked):
    """Grover Oracle operator"""
    ## Define circuit with n qubits
    qc = QuantumCircuit(n, name="Oracle")
    for target in marked:
        zeros = [i for i, bit in enumerate(reversed(target)) if bit == "0"]
        if zeros:
            qc.x(zeros)
        phase_flip(qc, n)
        if zeros:
            qc.x(zeros)
    return qc
 
 
def diffuser(n):
    """Grover diffusion operator"""
    qc = QuantumCircuit(n, name="Diffuser")
    qc.h(range(n))
    qc.x(range(n))
    phase_flip(qc, n)
    qc.x(range(n))
    qc.h(range(n))
    return qc


def grover_circuit(n, marked, iterations):
    qc = QuantumCircuit(n)
    qc.h(range(n))
    orc, dif = oracle(n, marked), diffuser(n)
    for _ in range(iterations):
        qc.compose(orc, inplace=True)
        qc.compose(dif, inplace=True)
    return qc


def main():

    if len(sys.argv) > 2:
        n = int(sys.argv[1])
        marked = sys.argv[2:]
    else:
        n, marked = 3, ["101"]

    assert all(len(m) == n and set(m) <= {"0", "1"} for m in marked), \
        f"Marked states must be {n}-bit binary strings"

    N, M = 2 ** n, len(marked)
    optimal = max(1, math.floor(math.pi / 4 * math.sqrt(N / M)))

    print(f"Qubits: {n}  |  Search space: {N}  |  Marked: {marked}")
    print(f"Optimal number of Grover iterations: {optimal}\n")

    ## Success probability after each iteration (exact, from statevector)
    for k in range(0, optimal + 3):
        sv = Statevector(grover_circuit(n, marked, k))
        probs = sv.probabilities_dict()
        p_success = sum(probs.get(m, 0.0) for m in marked)
        print(f"{p_success:.4f}")

    ## Sampled like real measurement
    qc = grover_circuit(n, marked, optimal)
    #print("\nCircuit:")
    #print(qc.draw(fold=120))

    shots = 1024
    counts = Statevector(qc).sample_counts(shots)
    for state, c in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"\n{state}/{shots}: {c:>4}")


if __name__ == "__main__":
    main()
