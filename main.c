#define _GNU_SOURCE
#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>
#include <unistd.h>
#include <errno.h>
#include <sched.h>
#include <string.h>
#include <sys/wait.h>
#include <sys/mount.h>
#include <sys/syscall.h>
#include <sys/stat.h>

#define stack_size 1024 * 1024
#define clone_flags CLONE_NEWPID
#define unshare_flags (CLONE_NEWIPC | CLONE_NEWNET | CLONE_NEWNS | CLONE_NEWUTS)

int init_process(void *root)
{
    // Build the path that will contain the filesystem pivot
    char *old_root = calloc(strlen(root) + strlen("/old-root") + 1, 1);
    if (old_root == NULL)
    {
        printf("init_process(): malloc: %d\n", errno);
        return 1;
    }
    strcat(old_root, root);
    strcat(old_root, "/old-root");

    if (mkdir(old_root, S_IRWXU | S_IRWXG) < 0)
    {
        if (errno != EEXIST)
        {
            printf("init_process(): mkdir(): %d\n", errno);
            return 1;
        }
    }

    // Create new namespaces
    if (unshare(unshare_flags) < 0)
    {
        printf("init_process(): unshare(): %d\n", errno);
        return 1;
    }

    if (sethostname("sub", 3) < 0)
    {
        printf("init_process(): Failed to set hostname");
    }

    // Mark the root drive as private, so changes in this namespace are not
    // propagated up to the parent namespace
    if (mount("", "/", NULL, MS_PRIVATE|MS_REC, NULL) < 0)
    {
        printf("init_process(): Failed to mark root as private\n");
        return 1;
    }

    if (mount(root, root, NULL, MS_BIND|MS_REC, NULL) < 0)
    {
        printf("init_process(): Failed to bind /subfs\n");
        return 1;
    }

    // Use pivot_root to jail this process inside of `root`
    if (syscall(SYS_pivot_root, root, old_root)< 0) {
        printf("init_process(): pivot_root failed: %d\n", errno);
        return 1;
    }

    if (chdir("/") < 0) {
        printf("init_process(): chdir failed\n");
        return 1;
    }

    // Unmount the pivot point (i.e. make the host's root unreachable from
    // within the container)
    if (umount2("/old-root", MNT_DETACH) < 0)
    {
        printf("init_process(): umount2(): %d\n", errno);
        return 1;
    }

    char *busybox_argv[] = { "sh", NULL };
    execvp("/busybox", busybox_argv);
    printf("init_process(): execvp(): %d\n", errno);
    return 1;
}

int main(int argc, char **argv)
{
    if (argc < 2)
    {
        printf("usage: %s <root>\n", argv[0]);
    }

    void *stack = malloc(stack_size);
    if (stack == 0)
    {
        printf("main(): malloc(): %d\n", errno);
        return 1;
    }
    void *stack_base = (void*)((uint64_t)stack + (uint64_t)stack_size); 

    pid_t pid = clone(init_process, stack_base, CLONE_NEWPID | SIGCHLD, argv[1]);
    if (pid < 0)
    {
        printf("main(): clone(): %d\n", errno);
        return 1;
    }

    waitpid(pid, NULL, 0);
    return 0;
}
