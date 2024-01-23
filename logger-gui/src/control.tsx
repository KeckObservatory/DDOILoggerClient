import Button from '@mui/material/Button'
import Stack from '@mui/material/Stack'
import Switch from '@mui/material/Switch'
import TextField from '@mui/material/TextField'
import React, { useEffect } from 'react'
import { GetLogsArgs, log_functions } from './api/api_root'
import { Log } from './log_view'
import { BooleanParam, NumberParam, StringParam, useQueryParam, withDefault } from 'use-query-params'
import { LocalizationProvider } from '@mui/x-date-pickers'
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import dayjs from 'dayjs';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker'

interface Props {
    setLogs: Function
}

const label = { inputProps: { 'aria-label': 'Switch demo' } };

export const Control = (props: Props) => {

    const [n_logs, setNLogs] = useQueryParam('n_logs', withDefault(NumberParam, 100))
    const [minutes, setMinutes] = useQueryParam('log_minutes', withDefault(NumberParam, 10))
    const [minuteSwitch, setMinuteSwitch] = useQueryParam('minute_switch', withDefault(BooleanParam, false))
    const [loggername, setLoggername] = useQueryParam('loggername', withDefault(StringParam, 'ddoi'))
    // const [startdatetime, setStartdatetime] = useQueryParam('startdate', 
    // withDefault(StringParam, dayjs().format('YYYY-MM-DDTHH:mm:ss')))
    // const [enddatetime, setEnddatetime] = useQueryParam('enddate', 
    // withDefault(StringParam, dayjs().format('YYYY-MM-DDTHH:mm:ss')))
    const [startdatetime, setStartdatetime] = useQueryParam<string>('startdatetime')
    const [enddatetime, setEnddatetime] = useQueryParam<string>('enddatetime')

    useEffect(() => {
        query_logs()
    }, [])

    const query_logs = async () => {
        const ln = loggername === 'ddoi' || loggername === 'koa' ? loggername : 'ddoi'
        let logs: Log[] = []
        let params: GetLogsArgs = {n_logs: n_logs, loggername: ln}
        params['minutes'] = minutes ? minutes : undefined
        params['startdatetime'] = startdatetime ? startdatetime : undefined
        params['enddatetime'] = enddatetime ? enddatetime : undefined
        logs = await log_functions.get_logs(params)
        if (logs) {
            //format logs
            logs = logs.map((log: any) => {
                const _id = log._id
                log._id = _id.$oid
                const utc_received = log.utc_received.$date
                log.utc_received = utc_received
                return log as Log
            })
            props.setLogs(logs)
        }
    }

    const on_query_logs = () => {
        query_logs()
    }

    const on_switch_change = (event: React.ChangeEvent<HTMLInputElement>) => {
        console.log('switch', event.target.checked)
        setMinuteSwitch(event.target.checked)
    }

    const on_n_logs_change = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
        let value = Number(event.target.value)
        value = value <= 500 ? value : 500
        console.log("n_logs", event.target.value, value)
        setNLogs(value)
    }

    const on_loggername_change = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
        let value = event.target.value
        console.log("loggername", value)
        setLoggername(value)
    }

    const on_minutes_change = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
        let value = Number(event.target.value)
        value = value <= 100 ? value : 100
        console.log("minutes", event.target.value, value)
        setMinutes(value)
    }

    const dt_changed = (value: dayjs.Dayjs, type: string) => {
        console.log('type', type, 'value', value)
        type.includes('start') && setStartdatetime(value?.format('YYYY-MM-DDTHH:mm:ss'))
        type.includes('end') && setEnddatetime(value?.format('YYYY-MM-DDTHH:mm:ss'))
    }


    return (
        <Stack sx={{ marginBottom: '4px'}} direction="row" spacing={2}>
            <Switch {...label}
                checked={minuteSwitch}
                onChange={on_switch_change}
            />
            {minuteSwitch ?
                <TextField
                    label="get number of minutes"
                    onChange={on_minutes_change}
                    value={minutes}
                    inputProps={{ inputMode: 'numeric', pattern: '[0-9]*' }}
                /> :
                <TextField
                    label="number of logs"
                    onChange={on_n_logs_change}
                    value={n_logs}
                    inputProps={{ inputMode: 'numeric', pattern: '[0-9]*' }}
                />
            }
            <TextField
                label="logger name (ddoi or koa)"
                onChange={on_loggername_change}
                value={loggername}
            />
            <LocalizationProvider dateAdapter={AdapterDayjs}>
                <DateTimePicker 
                label='start time'
                onChange={(value: dayjs.Dayjs | null) => value && dt_changed(value, 'startdatetime')} 
                value={startdatetime ? dayjs(startdatetime as string): undefined} 
                views={['year', 'day', 'hours', 'minutes', 'seconds']} />
                <DateTimePicker 
                label='end time'
                onChange={(value: dayjs.Dayjs | null) => value && dt_changed(value, 'enddatetime')} 
                value={enddatetime ? dayjs(enddatetime as string) : undefined} 
                views={['year', 'day', 'hours', 'minutes', 'seconds']} />
                </LocalizationProvider>
            <Button variant={'contained'}
                onClick={on_query_logs}
            >Query Logs</Button>
        </Stack>
    )
}