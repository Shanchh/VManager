export interface Account {
    _id: string,
    email: string,
    nickname: string,
    role: string,
    createAt: number,
    VMisCreate: boolean,
    heartbeatCount: number
}
