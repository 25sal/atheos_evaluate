#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define NMAX 200
void nuovastr(char *,char *);
struct mystruct {
char  s1[NMAX];
char s2[NMAX];
int l1;
int l2;
} ;



typedef  struct mystruct MyStruct;


void stampa(MyStruct ms)
{
	printf("{%s, %s, %d, %d}\n", ms.s1, ms.s2, ms.l1, ms.l2);
	}

int main()
{
   MyStruct v[100];
   FILE *fp;
   char s1[NMAX],s2[NMAX];
   char *ps;
   int k=0;
   fp=fopen("input.txt","r");
   if(fp!=NULL)
   {
     do{
        ps=fgets(s1,NMAX,fp);
        if(ps!=NULL){
			printf("%s\n",s1);
			nuovastr(s1,s2);
        printf("%s\n",s2);
        v[k].l1=strlen(s1);
        v[k].l2=strlen(s2);
	memset(v[k].s1,0,NMAX);
	memset(v[k].s2,0,NMAX);
        strcpy(v[k].s1,s1);
        strcpy(v[k].s2,s2);
        k++;}
       }while(ps!=NULL);
       fclose(fp);

       fp=fopen("output.bin","w");
       if(fp!=NULL)
        { fwrite(v,sizeof(MyStruct),k,fp);
          fclose(fp);
          }
	  
	  for(int i=0;i<k;i++)
	     stampa(v[i]);

   }
   else
      printf("Errore apertura file\n");


    return 0;
}

int conta(char *s, char c){
  int cont=0;
  for(int i=0;i<strlen(s);i++)
    if(s[i]==c) cont++;
  return cont;

}

void nuovastr(char *s1,char *s2){
  int i=0; int j=0;
  s2[0]='\0';
  for(i=0;i<strlen(s1);i++)
  {
   if((s1[i]<='z') && (s1[i]>='a'))
   {
     if ( conta(s2,s1[i])==0)
     {
       s2[j++]=s1[i];
       s2[j++]=conta(s1,s1[i])+'0';

     }
   }

  }
   s2[j]='\0';

}
