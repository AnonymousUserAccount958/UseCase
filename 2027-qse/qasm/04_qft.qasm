// Quantum Fourier transform of |0101> (4 qubits)
OPENQASM 3.0;
include "stdgates.inc";
qubit[4] q;
/* Start group Input |0101> */
  x q[1];
  x q[3];
/* End group Input |0101> */
/* Start group QFT */
  /* Start group Rotations q0 */
    h q[0];
    cp(pi/2) q[1], q[0];
    cp(pi/4) q[2], q[0];
    cp(pi/8) q[3], q[0];
  /* End group Rotations q0 */
  /* Start group Rotations q1 */
    h q[1];
    cp(pi/2) q[2], q[1];
    cp(pi/4) q[3], q[1];
  /* End group Rotations q1 */
  /* Start group Rotations q2 */
    h q[2];
    cp(pi/2) q[3], q[2];
  /* End group Rotations q2 */
  /* Start group Rotations q3 */
    h q[3];
  /* End group Rotations q3 */
  /* Start group Swaps */
    swap q[0], q[3];
    swap q[1], q[2];
  /* End group Swaps */
/* End group QFT */
/* Measurement */
bit[4] c = measure q;
