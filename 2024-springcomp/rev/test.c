#include <stdio.h>
#include <string.h>

int main() {
    // 定義密碼
    char password[] = "Wh@l3120_thInking...";
    // 使用者輸入的密碼
    char input[50];
    
    // 提示用戶輸入密碼
    printf("Please enter the password: ");
    scanf("%s", input);
    
    // 比較輸入的密碼是否與預定密碼相符
    if (strcmp(input, password) == 0) {
        // 密碼正確
        printf("womp, correct!!!\n");
    } else {
        // 密碼錯誤
        printf("QwQ\n");
    }
    
    return 0;
}
