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

const LOGGER_BASE_URL = 'http://vm-appserver.keck.hawaii.edu/api/log/get_logs?'
const IS_BUILD= process.env.NODE_ENV === 'production'

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
    let url = LOGGER_BASE_URL
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
    get_logs: IS_BUILD ? get_logs: mock_get_logs
}