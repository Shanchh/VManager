export type Client = {
    username: string;
    client_id: string;
    vmcount: number;
    connected_at: number;
    connection_duration: number;
    ip: string
    role?: string;
}