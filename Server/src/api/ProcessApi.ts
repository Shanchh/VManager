import axios from "axios";

export const get_my_profile = async () => {
    try {
        const res = await axios.get("/get_my_profile");
        return res.data?.message;
    }
    catch (err) {
        throw err;
    }
}
