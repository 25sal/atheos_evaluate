#include <stdio.h>
#include <string.h>

#define N 100

struct mystruct{
char stringa[N];
int indice;
};


void printstruct(struct mystruct v)
{


	printf("{%s, %d }\n",v.stringa, v.indice);
	
	}

void legge_stringhe(char string[N][N],int *n, FILE *fpin);
void build_mat(char string[N][N],int n,int mat[N][N]);
void build_struct(char string[N][N],int n,struct mystruct v[N]);
void ordinamento(int mat[N][N],int n,struct mystruct v[N]);

int main(){
char string[N][N];
int mat[N][N];
int n;         //numero stringhe
struct mystruct v[N];
FILE *fpin,*fpout;

fpin=fopen("input.txt","r");
if(fpin==NULL){
    printf("IL FILE NON ESISTE");
}else{
legge_stringhe(string,&n,fpin);
}

build_mat(string,n,mat);
build_struct(string,n,v);
printf("\n");


fpout=fopen("output.bin","w");
if(fpout!=NULL){
    fwrite(v,sizeof(struct mystruct),n,fpout);
    printf("\nSALVATAGGIO AVVENUTO");
    fclose(fpout);;
}else{
printf("\nSALVATAGGIO NON AVVENUTO");
}
fpout=fopen("output.bin","r");
if(fpout!=NULL){
    fread(v,sizeof(struct mystruct),n,fpout);
    for(int i =0;i<n;i++)
       printstruct(v[i]);
    printf("\nSALVATAGGIO AVVENUTO");
    fclose(fpout);;
}else{
printf("\nSALVATAGGIO NON AVVENUTO");
}
}

void legge_stringhe(char string[N][N],int *n, FILE *fpin){
char * temp;
int i=0;
do{
    temp=fgets(string[i],N,fpin);
    i++;
}
while(temp!=NULL);
i--;
fclose(fpin);
*n=i;

for(int i=0;i<*n;i++){
    printf("%s\n",string[i]);
}
}

void build_mat(char string[N][N],int n,int mat[N][N]){
int j=0;
int parole=0,maiuscole=0,minuscole=0;
int cont=0;
int v[N];
int h,max,k=0;;
for(int i=0;i<n;i++){
        j=0;   //indice che scorre la stringa
        parole=0;    //conta parole
        maiuscole=0;  //conta maiuscole
        minuscole=0;  //conta minuscole
        cont=0;       //conta caratteri
        h=0;          //scorre vettore di appoggio
    while(string[i][j]!='\0' && string[i][j]!='\n'){
        if(string[i][j+1]==' ' || string[i][j+1]=='\0' || string[i][j+1]=='\n'){
            parole++;
            cont++;
            v[h]=cont;
            cont=0;
            h++;
        }else if(string[i][j]!=' ' && string[i][j]!='\0' && string[i][j]!='\n'){
        cont++;
        }

        if(string[i][j]>='A' && string[i][j]<='Z'){
            maiuscole++;
        }else if(string[i][j]>='a' && string[i][j]<='z'){
        minuscole++;
        }
        j++;

}
for(int l=0;l<parole;l++){
    max=v[l];
    if(v[l+1]>max){          //confronta gli elementi del vettore di appoggio per definire la parola più grande
        max=v[l];
    }
}
k=0;
    mat[i][k]=parole;
    k++;
    mat[i][k]=max;
    k++;
    mat[i][k]=maiuscole;
    k++;
    mat[i][k]=minuscole;
}
for(int i=0;i<n;i++){
     printf("\n");
    for(int j=0;j<4;j++){
        printf("%d ",mat[i][j]);
    }
}

}

void build_struct(char string[N][N],int n,struct mystruct v[N]){
int j=0;
for(int i=0;i<n;i++){
        j=0;
    memset(v[i].stringa, 0,N);
    while(string[i][j]!='\0' && string[i][j]!='\n'){
        v[i].stringa[j]=string[i][j];
        j++;
    }
       v[i].indice=i;
}
for(int i=0;i<n;i++){
    printf("\n%s",v[i].stringa);
    printf(" %d",v[i].indice);
}
}

void ordinamento(int mat[N][N],int n,struct mystruct v[N]){
int max;
struct mystruct temp; int tempm;
for(int i=0;i<n;i++){
    max=i;
    for(int j=i+1;j<n;j++){
        if(mat[j][1]>mat[max][1]){      //confronta gli elementi della seconda colonna per riordinare struct
        max=j;
        }
    }

     for(int k=0;k<n;k++)
      {
		tempm=mat[i][k];
		mat[i][k]=mat[max][k];
		mat[max][k]=tempm;
    }
     temp=v[i];
     v[i]=v[max];
     v[max]=temp;

}
for(int i=0;i<n;i++){
    printf("\n%s",v[i].stringa);
    printf(" %d",v[i].indice);
}
}
