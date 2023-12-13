# Simulation-of-Directory-based-Cache-Coherence

## Working

The simulator takes input as an instruction like `<core> <state> <address>` and updates the cache memory directory and data along with the main memory directory and data accordingly.
There are four cores, each having a cache, which is two-way associative, having four cache lines, and each line is byte addressable. The main memory directory contains state, owner and sharer bits of all 64 addresses along with the data present at that address.

All the updates in the cache are printed in a log file generated after executing each of the test cases, and after every test case, the memory directory is printed on the terminal.


## Assumptions & Semantics

- Invalid mem directory also if a core requests invalid instruction.
- Bit down after executing the instruction by that core & no owner change as if new instruction comes, it will change the owner by seeing the shared hot vector & update accordingly.
- Invalid instruction/address in cache is removed in checking for LRU.
- Initially invalidate state in memory directory.
- The Sharer bit of core 0 is the rightmost bit, and for core 3, the leftmost bit.

## Instructions

There are four types of instructions our Simulator can handle:

- `<Core> LS <address>`
- `<Core> LM <address>`
- `<Core> IN <address>`
- `<Core> ADD <address> #immediate`

## Build Instructions

To build the simulator, run the following command:

```bash
python .\Final-Code.py
