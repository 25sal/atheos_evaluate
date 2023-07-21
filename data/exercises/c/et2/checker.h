struct Mystruct
{
	
    float avg; 
    char id;
    int rc;
};


void printstruct(struct Mystruct v)
{


	printf("{%f, %c, %d}\n",v.avg, v.id, v.rc);
	
	}
