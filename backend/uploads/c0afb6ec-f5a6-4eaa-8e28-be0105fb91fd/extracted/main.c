
    #include <stdio.h>
    #include "utils.h"

    int global_var;  // MISRA violation: unused global

    int main() {
        int local_uninitialized;  // MISRA violation
        printf("Workflow test\n");
        return local_uninitialized;  // MISRA violation
    }
    