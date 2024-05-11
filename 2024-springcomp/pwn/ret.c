#include"stdio.h"
#include"stdlib.h"
#include"string.h"
#include <time.h>
void win(){
    system("cat flag.txt");
}
int main(){
    setvbuf(stdin, 0, _IONBF, 0);
    setvbuf(stdout, 0, _IONBF, 0);
    char s[16];
    puts("back2future~\n");
    gets(s);
    return;
}
