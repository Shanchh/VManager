import axios from "axios";

export const create_user = async (email: string, nickname: string) => {
    try {
        const res = await axios.post("/create_user", { email, nickname });
        return res.data;
    }
    catch (err) {
        throw err;
    }
}

export const get_my_profile = async (email: string | null) => {
    try {
        const res = await axios.post("/get_my_profile", { email });
        return res.data?.message;
    }
    catch (err) {
        throw err;
    }
}

export const get_all_account_data = async () => {
    try {
        const res = await axios.get("/get_all_account_data");
        return res.data.message;
    }
    catch (err) {
        throw err;
    }
}

export const list_connected = async () => {
    try {
        const res = await axios.get("/list_connected");
        return res.data.message;
    }
    catch (err) {
        throw err;
    }
}