
struct Mystruct
{
	char lettera;
	float frequenzaOccorrenza;	
	int numeroOccorrenze;
	int posizioniLettera[100];
};


void printstruct(struct Mystruct v)
{


	printf("{%c, %f, %d, [",v.lettera, v.frequenzaOccorrenza, v.numeroOccorrenze);
	for(int i=0;i<v.numeroOccorrenze && i<100;i++)
		printf("%d,", v.posizioniLettera[i]);
	printf("]}\n");
	
	}
