# EXTENDING WLANG W/ POINTER SUPPORT

## Introduction
This project extends the While Language (wlang) by introducing references, enabling advanced memory management and data
manipulation capabilities. References in programming languages allow
variables to be allocated on the heap and accessed indirectly, facilitating
dynamic memory allocation, data sharing, and modular program design.


Our implementation involves syntactic extensions for reference declaration (`ref x := new 42`) and dereferencing (`y := *x`). We modified
the Abstract Syntax Tree (AST) to include new nodes for reference related operations and updated the parser to recognize these new constructs. The interpreter was extended to manage a heap using a dictionary, enabling proper handling of references. Through rigorous testing with various test cases, we validated the functionality and correctness of our implementation.

This extension enhances wlang’s versatility
and power, making it suitable for more complex computational tasks.
The project showcases our design decisions, theoretical foundations, and
practical implementation challenges, culminating in a more robust and
capable language for users.

## Design Decisions
To introduce references, we decided on a simple and intuitive syntax which
closely follows notation standards prescribed by languages like C or C++ for
familiarity & ease-of-use.
We also added additional functionalities & commands like AddressOf and print_heap
so developers can easily debug their referencing-related code in-program itself.

1.  **Syntax for Reference Declaration**

    For declaring a reference, the keyword ’ref’ is used, followed by the variable name
    and the value it points to:
    ```
    ref x := new 42
    ```
2. **Syntax for Dereferencing**

    Dereferencing a reference, i.e., accessing the value it points to, is done using the
    ’*’ operator:
    ```
    y := *x
    ```

3. **Syntax for AddressOf (Additional Feature)**

   To get the memory address of a variable and then store it in the pointer variable,
   we employ the ’&’ operator.
   ```
   z := &y
   ```

4. **Syntax for print_heap (Additional Feature)**

   To help debug and track heap memory utilization, we further extended the
   while language with a print_heap command to output the contents of the
   heap.
   ```
   print_heap
   ```

## How to Run the Project:

1. Clone the repository.
    ```
    git clone https://github.com/Kabiirk/WLANG_with_pointers.git
    ```
2. `cd` into the project root.
    ```
    cd WLANG_with_pointers
    ```
3. Install required packages.
    ```
    pip install -r requirements.txt
    ```
4. Run the Test `wlang` program  by executing the interpreter. here `test2.prg` contains the `wlang` program, you can edit it and write your own in this file or make your own:
    ```
    python3 -m wlang.int wlang/test2.prg
    ```

A working example:
Running the following command in the `WLANG_with_pointers/` folder:
```
~/...~/WLANG_with_pointers$ python3 -m wlang.int wlang/test2.prg
```

Should generate the following output (adresses may differ)
```
Pointer declared y with value 42 at address 9790272
Address of y: 9790272
Dereferencing pointer x with address 9790272 to value 42
y: 9790272
x: 9790272
z: 42

Heap:  {9790272: 42}
```

_Made in collaboration with Seturaj Matroja as a project for ECE 653 - Software Testing, Quality Assurance & Maintenance_