GIT_VERSION := $(shell git describe --tags)

OBJECTS = main.o

include ../include/generated/variables.mak
include $(SOC_DIRECTORY)/software/common.mak

CFLAGS += -Wall -Werror -I$(APPLICATION_DIRECTORY)/include
INCLUDES += -I$(BUILDINC_DIRECTORY)/generated

NAME = application

all: $(NAME).fbi $(NAME).bin

vpath %.a $(PACKAGES:%=../%)

# pull in dependency info for *existing* .o files
-include $(OBJECTS:.o=.d)

%.fbi: %.bin
	$(PYTHON) -m litex.soc.software.mkmscimg $< -f --little -o $@

%.bin: %.elf
	$(OBJCOPY) -O binary -S -R .bss $< $@
	chmod -x $@

$(NAME).elf: $(APPLICATION_DIRECTORY)/linker.ld $(OBJECTS)

%.elf: crt0.o $(OBJECTS)
	$(CC) $(LDFLAGS) \
		-T $(APPLICATION_DIRECTORY)/linker.ld \
		-N -o $@ \
		crt0.o \
		$(OBJECTS) \
		$(PACKAGES:%=-L../%) \
		-Wl,--whole-archive \
		-Wl,--gc-sections \
		$(LIBS:lib%=-l%)
	chmod -x $@
	$(PYTHON) -m litex.soc.software.memusage $@ ../include/generated/regions.ld $(TRIPLE)

%.o: $(APPLICATION_DIRECTORY)/src/%.c
	$(compile)

%.o: %.c
	$(compile)

%.o: $(APPLICATION_DIRECTORY)/src/%.S
	$(assemble)

crt0.o: $(CPU_DIRECTORY)/crt0.S
	$(assemble)

clean:
	$(RM) $(OBJECTS) $(OBJECTS:.o=.d) $(NAME).elf $(NAME).fbi .*~ *~

.PHONY: all clean load
