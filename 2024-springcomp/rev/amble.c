#include"stdio.h"
#include"stdlib.h"
#include"string.h"
void fake_func(){
printf("I SEE, YOU WANT THE FLAG : ICED{FAKE_FLAG}\n");
}
void true_func(){
char c[48];
int a[48]={514, 472, 486, 479, 864, 528, 710, 710, 773, 668, 780, 829, 808, 710, 801, 829, 682, 815, 738, 780, 773, 668, 682, 773, 703, 668, 689, 682, 689, 850, 668, 801, 710, 829, 710, 801, 808, 710, 668, 808, 752, 738, 759, 759, 668, 619, 479, 878};
scanf("%s", c);
for(int i=0;i<48;i++){
if((int)c[i]*7+3!=a[i]){
printf("No, no, no...\n");
return 0;
}
}
printf("Bring me some cakes!\n");
return 0;
}
int main(){
fake_func();
return 0;
}
