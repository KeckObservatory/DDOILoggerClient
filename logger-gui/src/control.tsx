import Button from '@mui/material/Button'
import Stack from '@mui/material/Stack'
import TextField from '@mui/material/TextField'
import React, { useEffect } from 'react'
import { GetLogsArgs, log_functions } from './api/api_root'
import { Log } from './log_view'
import { NumberParam, StringParam, useQueryParam, withDefault } from 'use-query-params'
import { LocalizationProvider } from '@mui/x-date-pickers'
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import dayjs from 'dayjs';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker'
import { Tooltip } from '@mui/material'

interface Props {
    setLogs: Function
}

const FORMAT = 'YYYY-MM-DDTHH:mm:ss'

export const Control = (props: Props) => {

    const [n_logs, setNLogs] = useQueryParam('n_logs', withDefault(NumberParam, 100))
    const [minutes, setMinutes] = useQueryParam('log_minutes', withDefault(NumberParam, 10))
    const [loggername, setLoggername] = useQueryParam('loggername', withDefault(StringParam, 'ddoi'))
    const [startdatetime, setStartdatetime] = useQueryParam<string | undefined>('startdatetime')
    const [enddatetime, setEnddatetime] = useQueryParam<string | undefined>('enddatetime')

    useEffect(() => {
        query_logs()
    }, [])

    const query_logs = async () => {
        const ln = loggername === 'ddoi' || loggername === 'koa' ? loggername : 'ddoi'
        let logs: Log[] = []
        let params: GetLogsArgs = { n_logs: n_logs, loggername: ln }
        params['minutes'] = minutes > 0 ? minutes : undefined
        params['startdatetime'] = dayjs(startdatetime, FORMAT, true).isValid() ? startdatetime : undefined
        params['enddatetime'] = dayjs(enddatetime, FORMAT, true).isValid() ? enddatetime : undefined
        console.log('params', params)
        logs = await log_functions.get_logs(params)
        const isString = typeof logs === 'string'
        console.log('logs', logs)
        if (!isString) {
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
        else {
            props.setLogs([])
        }
    }

    const on_query_logs = () => {
        query_logs()
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

    const dt_changed = (value: dayjs.Dayjs | null | undefined, type: string) => {
        console.log('type', type, 'value', value)
        type.includes('start') && setStartdatetime(value?.format(FORMAT))
        type.includes('end') && setEnddatetime(value?.format(FORMAT))
    }


    return (
        <Stack sx={{ marginBottom: '4px' }} direction="row" spacing={2}>
            <Tooltip title="get logs from n minutes ago (or from start date if defined)">
                <TextField
                    label="minutes"
                    onChange={on_minutes_change}
                    value={minutes}
                    inputProps={{ inputMode: 'numeric', pattern: '[0-9]*' }}
                />
            </Tooltip>
            <Tooltip title="set limit to n logs">
                <TextField
                    label="number of logs"
                    onChange={on_n_logs_change}
                    value={n_logs}
                    inputProps={{ inputMode: 'numeric', pattern: '[0-9]*' }}
                />
            </Tooltip>
            <TextField
                label="logger name (ddoi or koa)"
                onChange={on_loggername_change}
                value={loggername}
            />
            <LocalizationProvider dateAdapter={AdapterDayjs}>
                <React.Fragment>
                    <DateTimePicker
                        label='start time'
                        slotProps={{
                            actionBar: {
                                actions: ['clear'],
                            },
                        }}
                        onChange={(value: dayjs.Dayjs | null) => dt_changed(value, 'startdatetime')}
                        value={startdatetime ? dayjs(startdatetime as string) : undefined}
                        views={['year', 'day', 'hours', 'minutes', 'seconds']} />
                    <DateTimePicker
                        slotProps={{
                            actionBar: {
                                actions: ['clear'],
                            },
                        }}
                        label='end time'
                        onChange={(value: dayjs.Dayjs | null) => dt_changed(value, 'enddatetime')}
                        value={enddatetime ? dayjs(enddatetime as string) : undefined}
                        views={['year', 'day', 'hours', 'minutes', 'seconds']} />
                </React.Fragment>
            </LocalizationProvider>
            <Button variant={'contained'}
                onClick={on_query_logs}
            >Query Logs</Button>
        </Stack>
    )
}