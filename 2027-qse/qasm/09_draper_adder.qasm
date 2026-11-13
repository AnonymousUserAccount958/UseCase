// Draper QFT adder, b := a + b mod 8 with a = 3, b = 2 (6 qubits)
OPENQASM 3.0;
include "stdgates.inc";
qubit[6] q;
/* Start group Encode a = 3 */
  x q[1];
  x q[2];
/* End group Encode a = 3 */
/* Start group Encode b = 2 */
  x q[4];
/* End group Encode b = 2 */
/* Start group Adder */
  /* Start group QFT(b) */
    h q[3];
    cp(pi/2) q[4], q[3];
    cp(pi/4) q[5], q[3];
    h q[4];
    cp(pi/2) q[5], q[4];
    h q[5];
    swap q[3], q[5];
  /* End group QFT(b) */
  /* Start group Add a */
    cp(pi) q[2], q[3];
    cp(pi) q[1], q[4];
    cp(pi/2) q[2], q[4];
    cp(pi) q[0], q[5];
    cp(pi/2) q[1], q[5];
    cp(pi/4) q[2], q[5];
  /* End group Add a */
  /* Start group Inverse QFT(b) */
    swap q[3], q[5];
    h q[5];
    cp(-pi/2) q[5], q[4];
    h q[4];
    cp(-pi/4) q[5], q[3];
    cp(-pi/2) q[4], q[3];
    h q[3];
  /* End group Inverse QFT(b) */
/* End group Adder */
/* Measurement of the result register b = q[3..5] (q[0..2] still hold a) */
bit[3] c;
c[0] = measure q[3];
c[1] = measure q[4];
c[2] = measure q[5];
