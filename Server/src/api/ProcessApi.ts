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
