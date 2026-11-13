// W state (3 qubits)
OPENQASM 3.0;
include "stdgates.inc";
qubit[3] q;
/* Start group Amplitude distribution */
  ry(1.9106332362490184) q[0];
  ch q[0], q[1];
/* End group Amplitude distribution */
/* Start group Entanglement */
  cx q[1], q[2];
  cx q[0], q[1];
/* End group Entanglement */
/* Start group Basis correction */
  x q[0];
/* End group Basis correction */
/* Measurement */
bit[3] c = measure q;
