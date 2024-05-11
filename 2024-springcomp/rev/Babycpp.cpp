#include<bits/stdc++.h>
using namespace std;
int main(){
    string password;
    int a[42]={72, 66, 68, 69, 122, 85, 105, 100, 94, 100, 96, 114, 104, 100, 114, 117, 94, 103, 109, 96, 102, 94, 117, 110, 94, 100, 96, 115, 111, 94, 72, 94, 102, 116, 100, 114, 114, 94, 89, 69, 32, 124};
    cin >> password;
    for(int i=0;i<42;i++){
        if((password[i]^a[i])!=1){
            cout << "Wrong password QQ\n";
            return 0;
        }
    }
    cout << "Password Correct!\n";
    return 0;
}
