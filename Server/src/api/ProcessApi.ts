import axios from "axios";
import { apiError } from "./HandleError";

export const create_user = async (email: string, nickname: string) => {
    try {
        const res = await axios.post("/create_user", { email, nickname });
        return res.data;
    }
    catch (err) {
        apiError(err)
        throw err;
    }
}

export const get_my_profile = async (email: string | null) => {
    try {
        const res = await axios.post("/get_my_profile", { email });
        return res.data?.message;
    }
    catch (err) {
        apiError(err)
        throw err;
    }
}

export const get_my_data = async () => {
    try {
        const res = await axios.post("/get_my_data");
        return res.data?.message;
    }
    catch (err) {
        apiError(err)
        throw err;
    }
}

export const get_all_account_data = async () => {
    try {
        const res = await axios.post("/get_all_account_data");
        return res.data.message;
    }
    catch (err) {
        apiError(err)
        throw err;
    }
}

export const list_connected = async () => {
    try {
        const res = await axios.post("/list_connected");
        return res.data.message;
    }
    catch (err) {
        apiError(err)
        throw err;
    }
}

export const call_operation = async (command: any) => {
    try {
        const res = await axios.post("/api", command);
        return res.data.message;
    }
    catch (err) {
        apiError(err)
        throw err;
    }
}

export const register_vmware = async () => {
    try {
        const res = await axios.post("/register_vmware");
        return res.data.message;
    }
    catch (err) {
        apiError(err)
        throw err;
    }
}

export const get_my_20_activities = async () => {
    try {
        const res = await axios.post("/get_my_20_activities");
        return res.data.message;
    }
    catch (err) {
        apiError(err)
        throw err;
    }
}

export const call_oneclick_operation = async (command: any) => {
    try {
        const res = await axios.post("/oneclick_operation", command);
        return res.data.message;
    }
    catch (err) {
        apiError(err)
        throw err;
    }
}

export const call_oneclick_broadcast = async (command: any) => {
    try {
        const res = await axios.post("/oneclick_broadcast", command);
        return res.data.message;
    }
    catch (err) {
        apiError(err)
        throw err;
    }
}

export const delete_account = async (data: any) => {
    try {
        const res = await axios.post("/delete_account", data);
        return res.data.message;
    }
    catch (err) {
        apiError(err)
        throw err;
    }
}

export const get_server_logs = async (level: string) => {
    try {
        const command = {
            level: level
        }
        const res = await axios.post("/get_server_logs", command);
        return res.data.message;
    }
    catch (err) {
        apiError(err)
        throw err;
    }
}

export const get_average_daily_count = async () => {
    try {
        const res = await axios.post("/get_average_daily_count");
        return res.data.message;
    }
    catch (err) {
        apiError(err)
        throw err;
    }
}

export const modify_user_role = async (command: any) => {
    try {
        const res = await axios.post("/modify_user_role", command);
        return res.data.message;
    }
    catch (err) {
        apiError(err)
        throw err;
    }
}

export const post_custom_command = async (command: any) => {
    try {
        const res = await axios.post("/post_custom_command", command);
        return res.data.message;
    }
    catch (err) {
        apiError(err)
        throw err;
    }
}

export const call_update_client = async (command: any) => {
    try {
        const res = await axios.post("/call_update_client", command);
        return res.data.message;
    }
    catch (err) {
        apiError(err)
        throw err;
    }
}

export const get_user_log_counts_data = async (command: any) => {
    try {
        const res = await axios.post("/get_user_log_counts_data", command);
        return res.data.data;
    }
    catch (err) {
        apiError(err)
        throw err;
    }
}

export const get_user_log_data = async (command: any) => {
    try {
        const res = await axios.post("/get_user_log_data", command);
        return res.data.data;
    }
    catch (err) {
        apiError(err)
        throw err;
    }
}