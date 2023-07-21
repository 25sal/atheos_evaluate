#define N 100
struct Mystruct{
char stringa[N];
int indice;
};


void printstruct(struct Mystruct v)
{


	printf("{%s, %d }\n",v.stringa, v.indice);
	
	}
