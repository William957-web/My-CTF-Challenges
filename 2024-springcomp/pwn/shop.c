#include"stdio.h"
#include"stdlib.h"
#include"string.h"
#include <time.h>
int y;
int main(){
    setvbuf(stdin, 0, _IONBF, 0);
    setvbuf(stdout, 0, _IONBF, 0);
    time_t t;
    srand((unsigned) time(&t));
    int items[3]={30, 40, 50}, x=1337;
    y=rand();
    printf("You have a chance to change a price for an item\nItem1:30$\nItem2:40$\nItem3:50$\n");
    int user, price;
    scanf("%d", &user);
        printf("Sure, input the final price!\n");
        scanf("%d", &price);
        items[user]=price;
    if(x==y){
        system("cat flag.txt");
    }
    return 0;
}
