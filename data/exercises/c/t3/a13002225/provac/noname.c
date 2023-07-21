#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct Stringa{
    char sottostringa[100];
    int pos_prima;
    char carattere[1];

}sottostringa;

void leggi_file(char v1[]);
void elabora_stringa(char v1[], int *num_ele, sottostringa vettore[]);
void scrivi_binario(sottostringa vettore[], int* num_ele);


int main(){
    char v1[100];
    int num_ele=0;
    sottostringa vettore[20];
    leggi_file(v1);
    elabora_stringa(v1, &num_ele, vettore);
    scrivi_binario(vettore, &num_ele);

    printf("%s\n", vettore[0].sottostringa);
    printf("%d\n", vettore[0].pos_prima);
    printf("%c", vettore[0].carattere[0]);







}


void leggi_file(char v1[]){
    char appoggio[100];

    FILE *fp;
    fp=fopen("input.txt", "r");

    fgets(appoggio, 100, fp);

    strcpy(v1, appoggio);

    fclose(fp);

}


void elabora_stringa(char v1[], int *num_ele, sottostringa vettore[]){
    char appoggio2[100][100];
    char appoggio[1];

    int i=0;
    while(v1[i]!='\0'){
        if(v1[i]==v1[i+1]){
            appoggio[0]=v1[i+1];
            v1[i+1]='-';
            for(int j=i+2; v1[j]!='\0'; j++){
                v1[j]=appoggio[0];
                appoggio[0]=v1[j+1];
            }
        }
        i++;
    }

int a=0;
for(int b=0; v1[b]!='\0'; b++){
        appoggio2[a][b]=v1[b];
    if(v1[b]=='-' || v1[b]=='.' || v1[b]==' ' && b==20){
        strcpy(vettore[*num_ele].sottostringa, &appoggio2[a]);
        vettore[*num_ele].pos_prima=b-strlen(&appoggio2[a]);
        if(vettore[*num_ele].pos_prima==-1){
            vettore[*num_ele].carattere[0]='\0';
        }else{
            vettore[*num_ele].carattere[0]=v1[b-1];
        }
        (*num_ele)++;
        a++;
    }

}






}





void scrivi_binario(sottostringa vettore[], int *num_ele){
    FILE *fd;
    fd=fopen("output.bin", "w");

    for(int i=0; i<(*num_ele); i++){
       fwrite(&vettore[i], sizeof(sottostringa), 20, fd);
    }




    fclose(fd);








}
