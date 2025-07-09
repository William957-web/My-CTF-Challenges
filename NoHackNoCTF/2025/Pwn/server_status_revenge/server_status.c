#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <time.h>
#include <pwd.h>
#include <grp.h>

#define SHM_SIZE 1024
#define DEFAULT_COMMAND "/usr/bin/dmesg"

key_t write_command_to_shm(const char *command) {
    key_t shm_key;
    int shmid;
    char *shm_addr;
    
    srand(time(NULL));
    shm_key = rand() % 0xfffff;
    
    shmid = shmget(shm_key, SHM_SIZE, IPC_CREAT | 0666);
    if (shmid == -1) {
        perror("shmget failed");
        return -1;
    }
    
    shm_addr = (char *)shmat(shmid, NULL, 0);
    if (shm_addr == (char *)-1) {
        perror("shmat failed");
        return -1;
    }
    
    strncpy(shm_addr, command, SHM_SIZE - 1);
    shm_addr[SHM_SIZE - 1] = '\0';
    
    shmdt(shm_addr);
    
    //printf("Command stored in shared memory with key: 0x%X\n", shm_key);
    return shm_key;
}

char *read_command_from_shm(key_t shm_key) {
    int shmid;
    char *shm_addr;
    char *command;
    
    shmid = shmget(shm_key, SHM_SIZE, 0666);
    if (shmid == -1) {
        perror("shmget failed");
        return NULL;
    }
    
    shm_addr = (char *)shmat(shmid, NULL, 0);
    if (shm_addr == (char *)-1) {
        perror("shmat failed");
        return NULL;
    }
    
    command = malloc(strlen(shm_addr) + 1);
    if (command) {
        strcpy(command, shm_addr);
    }
    
    shmdt(shm_addr);
    
    return command;
}

void clear_shared_memory(key_t shm_key) {
    int shmid;
    
    shmid = shmget(shm_key, SHM_SIZE, 0666);
    if (shmid != -1) {
        shmctl(shmid, IPC_RMID, NULL);
    }
}

void print_stars(void) {
    const int total = 40;
    const useconds_t delay = 50000;  // 50,000 microseconds = 0.05 seconds

    for (int i = 0; i < total; i++) {
        putchar('*');
        fflush(stdout);
        usleep(delay);
    }
    putchar('\n');
}


void escalate_privileges() {
    
    if (setuid(0) == -1) {
        perror("setuid failed");
    }
    if (setgid(0) == -1) {
        perror("setgid failed");
    }
    if (seteuid(0) == -1) {
        perror("seteuid failed");
    }
    if (setegid(0) == -1) {
        perror("setegid failed");
    }
    
    printf("Running with elevated privileges (UID: %d, GID: %d)\n", getuid(), getgid());
}

int execute_command(const char *command) {
    FILE *fp;
    char buffer[1024];
    
    
    fp = popen(command, "r");
    if (fp == NULL) {
        perror("popen failed");
        return 0;
    }
    
    printf("=== Command Output ===\n");
    while (fgets(buffer, sizeof(buffer), fp) != NULL) {
        printf("%s", buffer);
    }
    printf("=== End of Output ===\n");
    
    pclose(fp);
    return 1;
}

int main() {
    key_t shm_key;
    char *command_from_shm;
    
    printf("=== Server Status Monitor v1.0 ===\n");
    printf("System diagnostic tool with root privileges\n\n");
    
    shm_key = write_command_to_shm(DEFAULT_COMMAND);
    if (shm_key == -1) {
        printf("Failed to store command in shared memory\n");
        return 1;
    }
    
    escalate_privileges();
    
    printf("Initializing...\n");
    printf("Hacking Nasa...\n");
    print_stars();
    printf("Done!\n");
    command_from_shm = read_command_from_shm(shm_key);
    if (!command_from_shm) {
        printf("Failed to retrieve command from shared memory\n");
        clear_shared_memory(shm_key);
        return 1;
    }
    
    
    if (!execute_command(command_from_shm)) {
        printf("Command execution failed!\n");
        free(command_from_shm);
        clear_shared_memory(shm_key);
        return 1;
    }
    
    free(command_from_shm);
    clear_shared_memory(shm_key);
    
    printf("\nSystem status check completed successfully!\n");
    return 0;
}                       