#include <stdio.h>
#include <stdlib.h>

int g_global_var = 0;

void unused_function() {
    printf("This function is never called\n");
}

int main() {
    int x;
    int *ptr = NULL;
    
    printf("Hello World\n");
    
    if (ptr) {
        *ptr = 10;
    }
    
    return x;
}
