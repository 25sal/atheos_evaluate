#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include "checker.h"



int main(int argc, char ** argv)
{
	struct Mystruct v1,v2;
	FILE *fpuser,*fptest;
	
	if(argc<2)
	 printf("usage: %s testoutput\n",argv[0]);
	else
	{
		
	if(argc==3)
	 fpuser=fopen(argv[2], "r");
	else
	 fpuser=fopen("output.bin","r");
	if(fpuser!=NULL)
	{
		int i=0, j=0;
		fptest=fopen(argv[1],"r");
		if(fptest!=NULL)
		{
			int n;
			do {
				n=fread(&v1,sizeof(struct Mystruct),1,fptest);
				if(n>0){
					int k =fread(&v2,sizeof(struct Mystruct),1,fpuser);
					if((k>0)&&(memcmp(&v1,&v2,sizeof(struct Mystruct))==0))
						{
							j++;
							}
					else if(strstr(argv[1],"3.in_out")!=NULL){
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
	if((j==i)&&(i>0))
		printf("TEST_SUPERATO, %d/%d elementi esatti\n",j,i);
	else
	   printf("TEST_NON_SUPERATO, %d/%d elementi esatti\n",j,i);

	}
	else
	  printf("output.bin not found\n");
  }
}
