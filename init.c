#define _GNU_SOURCE
#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>
#include <unistd.h>
#include <errno.h>
#include <sched.h>
#include <string.h>
#include <sys/wait.h>
#include <sys/stat.h>
#include "init.h"
#include "filesystem.h"
#include "network.h"

#define stack_size 1024 * 1024
#define clone_flags CLONE_NEWPID
#define unshare_flags (CLONE_NEWIPC | CLONE_NEWNET | CLONE_NEWNS | CLONE_NEWUTS)

int init_proc(void *arg)
{
    container_spec_t *cspec = (container_spec_t*)arg;

    // Build the path that will contain the filesystem pivot and
    // ensure it exists on disk
    char *pivot = "/.pivot";
    char *pivot_abs = calloc(strlen(cspec->root) + strlen(pivot) + 1, 1);
    if (pivot_abs == NULL)
    {
        return 1;
    }
    strcat(pivot_abs, cspec->root);
    strcat(pivot_abs, pivot);

    if (mkdir(pivot_abs, S_IRWXU | S_IRWXG) < 0)
    {
        if (errno != EEXIST)
        {
            printf("init_proc(): mkdir(): %d\n", errno);
            return 1;
        }
    }

    // Create and enter new namespaces
    if (unshare(unshare_flags) < 0)
    {
        printf("init_proc(): unshare(): %d\n", errno);
        return 1;
    }

    if (setup_network("sub") < 0)
    {
        printf("init_proc(): setup_network() failed\n");
        return 1;
    }

    if (setup_filesystem(cspec->root, pivot, pivot_abs) < 0)
    {
        printf("init_proc(): setup_filesystem() failed\n");
        return 1;
    }

    return run_entry_point(cspec->entry_point, cspec->entry_point_argv);
}

int run_entry_point(char *entry_point, char **argv)
{
    execvp(entry_point, argv);

    printf("run_entry_point(): execvp(): %d\n", errno);
    return -1;
}

int spawn_init_proc(char *root, char *entry_point, char **entry_point_argv)
{
    container_spec_t *cspec = malloc(sizeof(container_spec_t));
    cspec->root = root;
    cspec->entry_point = entry_point;
    cspec->entry_point_argv = entry_point_argv;

    void *stack = malloc(stack_size);
    if (stack == 0)
    {
        printf("spawn_init_proc(): malloc(): %d\n", errno);
        return -1;
    }
    void *stack_base = (void*)((uint64_t)stack + (uint64_t)stack_size); 

    pid_t pid = clone(init_proc, stack_base, CLONE_NEWPID | SIGCHLD, cspec);
    if (pid < 0)
    {
        printf("spawn_init_proc(): clone(): %d\n", errno);
        return -1;
    }

    waitpid(pid, NULL, 0);
    return 0;
}
