#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
    if (argc != 6) {
        printf("Usage: %s i want the flag please\n", argv[0]);
        return 1;
    }
    
    if (strcmp(argv[1], "i") != 0 || 
        strcmp(argv[2], "want") != 0 || 
        strcmp(argv[3], "the") != 0 || 
        strcmp(argv[4], "flag") != 0 ||
        strcmp(argv[5], "please") != 0) {
        printf("Wrong arguments!\n");
        return 1;
    }
    
    puts("QnQSec{test_flag_by_whale120}\n");
    
    return 0;
}
