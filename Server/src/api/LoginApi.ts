import axios from "axios";

export const register_user = async (values: any) => {
    try {
        const res = await axios.post("/register", { values });
        return res.data?.message;
    }
    catch (err) {
        throw err;
    }
}

export const login_user = async (values: any) => {
    try {
        const res = await axios.post("/login", { values });
        console.log(res);
        return res.data;
    }
    catch (err) {
        throw err;
    }
}