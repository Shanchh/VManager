export interface Account {
    _id: string,
    email: string,
    nickname: string,
    role: string,
    createAt: number,
    VMisCreate: boolean,
    heartbeatCount: number
}

export interface LogUser {
    id: string,
    email: string,
    nickname: string
}

export interface Log {
    _id: string;
    timestamp: Date;
    level: string;
    action: string;
    requester: LogUser;
    recipient: LogUser | null;
    details: {
      message: string;
    };
    ipAddress: string;
  }