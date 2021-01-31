
build:
	mkdir -p ~/.local/bin
	cp investigate  ~/.local/bin
	cp log_investigation  ~/.local/bin	
	chmod +x ~/.local/bin/investigate
	chmod +x ~/.local/bin/log_investigation
	echo 'export PATH="$$PATH:$$HOME/.local/bin"' >> $$HOME/.bashrc
	cat bash_alias >> $$HOME/.bash_aliasesX

test:
	@echo "Testing: " 
	@investigate
