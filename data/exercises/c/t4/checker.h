#define NMAX 200
struct Mystruct
{
char  s1[NMAX];
char s2[NMAX];
int l1;
int l2;

}; 

void printstruct(struct Mystruct v)
{


	printf("{%s, %s, %d, %d}\n", v.s1, v.s2, v.l1, v.l2);
	
	}
