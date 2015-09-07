void hello() {
}

void foo() {
	hello();
}

void main()
{
	while(1) {
	foo();
	sleep(1);
    }
}
