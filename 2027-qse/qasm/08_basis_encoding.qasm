// Basis encoding of |1011> (4 qubits)
OPENQASM 3.0;
include "stdgates.inc";
qubit[4] q;
/* Start group Basis encoding |1011> */
  x q[0];
  x q[2];
  x q[3];
/* End group Basis encoding |1011> */
/* Measurement */
bit[4] c = measure q;
