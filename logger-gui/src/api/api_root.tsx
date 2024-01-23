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

export interface GetLogsArgs {
    n_logs: number,
    loggername: string,
    minutes?: number,
    subsystem?: string,
    semid?: string,
    startdatetime?: string,
    enddatetime?: string,
    dateformat?: string
}

export const get_logs = (
    args: GetLogsArgs
): Promise<Log[]> => {
    let url = import.meta.env.VITE_LOGGER_BASE_URL
    url += args.minutes ? `minutes=${args.minutes}` : `n_logs=${args.n_logs}`
    url += args.loggername ? `&loggername=${args.loggername}` : ""
    url += args.subsystem ? `&subystem=${args.subsystem}` : ""
    url += args.semid ? `&semid=${args.semid}` : ""
    url += args.startdatetime ? `&start_date=${args.startdatetime}` : ""
    url += args.enddatetime ? `&end_date=${args.enddatetime}` : ""
    url += args.dateformat ? `&date_format=${args.dateformat}` : "&date_format=%Y-%m-%dT%H:%M:%S"
    return axiosInstance.get(url)
        .then(handleResponse)
        .catch(handleError)
}


export const log_functions = {
    get_logs: import.meta.env.PROD ? get_logs: mock_get_logs
}