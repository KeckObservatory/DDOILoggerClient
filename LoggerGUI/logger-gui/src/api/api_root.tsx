import axios from 'axios';

import { handleResponse, handleError, intResponse, intError } from './response';
import { default as mock_logs } from './mock_logs.json'
import { Log } from '../log_view'

export const mock_get_logs = (
   ) => {
   const mockPromise = new Promise<Log[]>((resolve) => {
      resolve(mock_logs as Log[])
   })
   return mockPromise
}

const axiosInstance = axios.create({
    withCredentials: true,
    headers: {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json',
        'withCredentials': false,
    }
})
axiosInstance.interceptors.response.use(intResponse, intError);

export const get_logs = (
    n_logs: number,
    loggername: string,
    minutes?: number,
    subsystem?: string,
    semid?: string,
): Promise<Log[]> => {
    let url = import.meta.env.VITE_LOGGER_BASE_URL
    if (minutes) {
        url += `minutes=${n_logs}`
    }
    else {
        url += n_logs ? `n_logs=${n_logs}` : ""
    }
    url += loggername ? `&loggername=${loggername}` : ""
    url += subsystem ? `&subystem=${subsystem}` : ""
    url += semid ? `&semid=${semid}` : ""
    return axiosInstance.get(url)
        .then(handleResponse)
        .catch(handleError)
}

export const log_functions = {
    get_logs: import.meta.env.PROD ? get_logs: mock_get_logs
}