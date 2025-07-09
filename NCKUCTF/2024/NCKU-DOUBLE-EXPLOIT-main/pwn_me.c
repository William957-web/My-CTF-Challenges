#include "stdio.h"
#include "stdlib.h"
int main(int argc, char *argv[]){
    setvbuf(stdin, 0, _IONBF, 0);
    setvbuf(stdout, 0, _IONBF, 0);
    char input[1], check='w';
    memcpy(input, argv[1], 2);
    if (check=='#')printf("Meowing ");
    else printf("N0m N0m\n");
}
