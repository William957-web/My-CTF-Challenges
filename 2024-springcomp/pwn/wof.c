#include"stdio.h"
#include"stdlib.h"
#include"string.h"
void gift(){
    gets();
}
size_t readbuf(char *buf, size_t len)
{
    size_t i=0;
    while(i<len){
        if(read(0,&buf[i],1)!=1){
            break;
        }
        if(buf[i]=='\n'){
            buf[i] = 0;
            break;
        }
        i++;
    }
    return i;
}
int main(){
    setvbuf(stdin, 0, _IONBF, 0);
    setvbuf(stdout, 0, _IONBF, 0);
    char s[24], meow[24], c[24];
    c[0]=24;printf("===Whale Overflow Challenge===\n🐳🐋🐳🐋🐳🐋🐳\nWhat's Your name?\n");
    readbuf(s, 0x100);
    printf("Welcome ");printf(s);printf("\n");
    printf("Leave some messages~\n");
    readbuf(meow, c[0]);
    return 0;
}
