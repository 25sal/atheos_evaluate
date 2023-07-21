struct Mystruct
{
    int posizione;
    int valore;

}; 

void printstruct(struct Mystruct v)
{

	printf("{%d; ",v.posizione);
	printf("%d}\n",v.valore);
	
	}
