#include<stdio.h>
#include<stdlib.h>
#include<string.h>
struct Mystruct
{
    char str[100];
    char precedente;
    int posizione;

}; 

void printstruct(struct Mystruct v)
{

	printf("{%s; ",v.str);
	printf("%c;",v.precedente);
	printf("%d}\n",v.posizione);
	
	}

int main()
{
	struct Mystruct v1,v2;
	FILE *fpuser,*fptest;
	fpuser=fopen("output.bin","r");
	if(fpuser!=NULL)
	{
		int i=0, j=0;
		fptest=fopen("output1.bin","r");
		if(fptest!=NULL)
		{
			int n;
			do {
				n=fread(&v1,sizeof(struct Mystruct),1,fpuser);
				if(n>0){
					int k =fread(&v2,sizeof(struct Mystruct),1,fptest);
					if((k>0)&&(memcmp(&v1,&v2,sizeof(struct Mystruct))==0))
						{
							j++;
							}
					else{
						printf("Mi aspettavo:");
						printstruct(v1);
						printf("Ho trovato:");
						printstruct(v2);
						}
				
				 
				 i++;
			 }
			}while(n>0);
			
			fclose(fptest);
			}
	fclose(fpuser);
	
	printf("%d/%d elementi esatti\n",j,i);

	}
	else
	  printf("output.bin not found\n");
}
