#include<stdio.h>

struct Mystruct{
	int position;
	int value;};
	

void sort(int v[], int n)
{int temp;
	for(int i=0;i<n-1;i++)
	 for(int j=0;j<n-i-1;j++)
	    if(v[j]>v[j+1])
	    {
			
			temp=v[j];
			v[j]=v[j+1];
			v[j+1]=temp;
			}
	
	}
	
int main()
{
	int v[100];
	int n;
	struct Mystruct ov[100];
	FILE* fp=fopen("input.txt","r");
	if(fp!=NULL)
	{
		fscanf(fp,"%d", &n);
		for(int i=0;i<n;i++)
		  fscanf(fp,"%d",&v[i]);
		fclose(fp);
		}
	sort(v,n);
	for(int i=0;i<n;i++)
	  {
		  ov[i].position=i;
		  ov[i].value=v[i];
	  }
	 
	fp = fopen("output.bin","w"); 
	if(fp!=NULL)
	{
		fwrite(ov,sizeof(struct Mystruct),n,fp);
		fclose(fp);
		}
	
	}
