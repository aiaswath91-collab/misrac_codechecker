
#include <stdio.h>

int unused_var;  // MISRA violation: unused variable

int main() {
    int x;  // MISRA violation: uninitialized variable
    printf("Hello World\n");
    return x;  // MISRA violation: returning uninitialized variable
}
