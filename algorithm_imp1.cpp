#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>
#include <limits.h>
 
void scale(int *in, int scale_factor, size_t arrlen)
{
    unsigned int i = 0;
    for( ; i < arrlen ; i++ )
    {
        in[i] = scale_factor*in[i];
    }
}
 
int find_max(int *arr, size_t arrlen)
{
    int max = -INT_MAX;
 
    unsigned int i = 0;
    for( ; i < arrlen ; i++ )
    {
        if( arr[i] > max )
        {
            max = arr[i];
        }
    }
 
    return max;
}
 
int find_min(int *arr, size_t arrlen)
{
    int min = INT_MAX;
 
    unsigned int i = 0;
    for( ; i < arrlen ; i++ )
    {
        if( arr[i] < min )
        {
            min = arr[i];
        }
    }
 
    return min;
}
 
 
void square_array(int *in, size_t arrlen)
{
    unsigned int i = 0;
    for( ; i < arrlen ; i++ )
    {
        in[i] = in[i]*in[i];
    }
}
 
void divide_array(int *arr, int denominator, size_t arrlen)
{
    if(denominator == 0)
    {
        return;
    }
 
    unsigned int i = 0;
    for( ; i < arrlen ; i++ )
    {
        arr[i] = arr[i] / denominator;
    }
}
 
void offset_array(int *arr, int offset_value, size_t arrlen)
{
    unsigned int i = 0;
    for( ; i < arrlen ; i++ )
    {
        arr[i] = arr[i] + offset_value;
    }
}
 
void reverse_array(int *in, int *out, size_t arrlen)
{
    int *reversed = malloc(sizeof(int)*arrlen);
    for (int i = 0; i < arrlen; ++i)
    {
        reversed[i] = in[ (arrlen-1) - i ];
    }

    out = reversed;
}
 
int average_array(int *in, size_t arrlen)
{
    int sum = 0;
    for (int i = 0; i < arrlen; ++i)
    {
        sum += in[i];
    }
    return sum / arrlen;
}
 
void clamp_array(int *in, int min, int max, size_t arrlen)
{
    for (int i = 0; i < arrlen; ++i)
    {
        int val = in[i];
        if (val > max)
        {
            in[i] = max;
        }
        else if (val < min)
        {
            in[i] = min;
        }
    }
}
 
int find_min_index(int *in, size_t arrlen)
{
    int min = INT_MAX;
    int min_index = -1;
 
    unsigned int i = 0;
    for( ; i < arrlen ; i++ )
    {
        if( in[i] < min )
        {
            min = in[i];
            min_index = i;
        }
    }
 
    return min_index;
}
 
int find_max_index(int *in, size_t arrlen)
{
    int max = -INT_MAX;
    int max_index = -1;
 
    unsigned int i = 0;
    for( ; i < arrlen ; i++ )
    {
        if( in[i] > max )
        {
            max = in[i];
            max_index = i;
        }
    }
 
    return max_index;  
}
 
 
int Partition(int *arr, int start, int end);
 
void quicksort_internal(int *arr, int start, int end)
{
    if (start == end)
    {
        return;
    }
 
    int index = Partition(arr, start, end);
    if (index > start)
    {
        quicksort_internal(arr, start, index);
    }
 
    if (index < end)
    {
        quicksort_internal(arr, index + 1, end);
    }
}
 
int Partition(int *arr, int start, int end)
{
    int i = start, j = end, x = arr[start];
 
    while (i < j)
    {
        while (i < j && arr[j] >= x)
        {
            j--;
        }
        if (i < j)
        {
            arr[i++] = arr[j];
        }
 
        while (i < j && arr[i] < x)
        {
            i++;
        }
        if (i < j)
        {
            arr[j--] = arr[i];
        }
    }
    arr[i] = x;
 
    return i;
}
 
void quicksort(int *in, size_t arrlen)
{
    quicksort_internal(in, 0, arrlen-1);
}
 
#define FLAG (0x55)
int custom_filter(int value1, int value2, size_t arrlen)
{
    if(value1 & FLAG == value2)
    {
        return value1;
    }

    return value2;
}
 
 
int algorithm(int *arr1, int *arr2, size_t len)
{
 
    //find both maxes and mins for input arrays
    int min_arr1 = find_min(arr1, len);
    int min_arr2 = find_min(arr2, len);
 
    int max_arr1 = find_max(arr1, len);
    int max_arr2 = find_max(arr2, len);
 
    //find max and min indexes
    int min_index_arr1 = find_min_index(arr1, len);
    int min_index_arr2 = find_min_index(arr2, len);
 
    int max_index_arr1 = find_max_index(arr1, len);
    int max_index_arr2 = find_max_index(arr2, len);
 
    //find averages
    int average1 = average_array(arr1, len);
    int average2 = average_array(arr2, len);
 
    //shave off the average
    offset_array(arr1, len, -average1);
    offset_array(arr2, len, -average2);
 
    //depending on the average
    //square one and scale the
    //other by 2
    if(average1 > average2)
    {
        square_array(arr1, len);
        scale(arr2, len, 2);
    }
    else
    {
        square_array(arr2, len);
        scale(arr1, len, 2);        
    }
 
    //clamp both arrays
    const int clamp_amount = (1<<17);
    clamp_array(arr1, -clamp_amount, clamp_amount, len);
    clamp_array(arr2, -clamp_amount, clamp_amount, len);
 
    quicksort(arr1, len);
    quicksort(arr2, len);
 
    int *reversed_arr2 = (int*)malloc(sizeof(int)*len);
    reverse_array(arr2, reversed_arr2, len);
 
 
    for(int i = 0; i < len; i++)
    {
        arr1[i] = arr1[i] - reversed_arr2[i];
    }
 
    int prev_max_index = arr1[max_index_arr1] - max_arr1;
    int prev_min_index = arr1[min_index_arr1] - min_arr1;
 
    divide_array(arr1, len, (prev_min_index + prev_max_index)/2 );
 
    return average_array(arr1, len);
}
