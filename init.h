#ifndef _INIT_H
#define _INIT_H

typedef struct
{
    char *root;
    char *entry_point;
    char **entry_point_argv;
} container_spec_t;

int spawn_init_proc(char *root, char *entry_point, char **entry_point_argv);
int init_proc(void *args);
int run_entry_point(char *entry_point, char **argv);

#endif
